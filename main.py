import uiautomator2 as u2
import xmltodict
import time
import pprint
import hashlib
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Import from our custom modules
from rl_agent import RLAgent
from ui_utils import get_all_components, find_edit_text, parse_bounds, get_basic_info, choose_from_pos
from prompt_generator import use_context_info_generate_prompt
from feedback_manager import load_feedback, save_feedback
from display_utils import show_hint

def main():
    """Main execution loop for connecting to the device, processing UI, and generating hints."""
    # --- CONFIGURATION ---
    # IMPORTANT: Update this path to where your T5 model is located on your computer.
    MODEL_PATH = '/Users/sanvishukla/Desktop/SRIP/fine-tuned-model-T5'
    # Set how many new feedback items to collect before retraining the model.
    TRAINING_INTERVAL = 5 
    
    print("Initializing tokenizer and model...")
    try:
        tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
        model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
    except Exception as e:
        print(f"FATAL ERROR: Could not load model or tokenizer from '{MODEL_PATH}'.")
        print(f"Please check the path. Details: {e}")
        return

    feedback_data = load_feedback()
    rl_agent = RLAgent(model, tokenizer)
    rl_agent.feedback_data = feedback_data

    # --- State Tracking Variables ---
    last_hierarchy_hash = None
    processed_components_on_screen = set()
    new_feedback_count = 0 

    # --- Main Application Loop ---
    while True:
        try:
            print('\nAttempting to connect to device...')
            d = u2.connect()
            print('Device connected successfully.')

            page_source = d.dump_hierarchy(compressed=True, pretty=True)
            
            # Check if the UI has changed since the last loop
            current_hash = hashlib.md5(page_source.encode('utf-8')).hexdigest()
            if current_hash == last_hierarchy_hash:
                print("UI has not changed. Waiting...")
                time.sleep(5) 
                continue
            
            # If UI has changed, reset the state
            print("\nUI has changed. Processing new screen...")
            last_hierarchy_hash = current_hash
            processed_components_on_screen.clear() 
            
            data_dict = xmltodict.parse(page_source)
            all_components = get_all_components(data_dict)
            actionable_components = [
                e for e in find_edit_text(data_dict) if not e.get('@content-desc')
            ]
            
            if not actionable_components:
                print("No input fields needing hints on this screen.")

            screen_height = d.info['displayHeight']
            screen_width = d.info['displayWidth']

            for e_component in actionable_components:
                bounds = e_component.get('@bounds', '')
                resource_id = e_component.get('@resource-id', '')
                component_id = f"{bounds}-{resource_id}"

                if component_id in processed_components_on_screen:
                    continue

                print('-----------------------------------------')
                pprint.pprint(e_component)
                
                dict_info = get_basic_info(e_component)
                nearby_components = choose_from_pos(all_components, bounds, screen_height, screen_width)
                dict_info['nearby-components'] = [get_basic_info(e_near) for e_near in nearby_components]
                
                final_text_prompt = use_context_info_generate_prompt(dict_info, screen_height, screen_width)
                print("\nGenerated Prompt for AI:\n", final_text_prompt)

                try:
                    generated_hint = rl_agent.generate_response(final_text_prompt)
                    
                    # --- CHANGE: Display hint prominently in the terminal ---
                    print("\n=========================================")
                    print(f" HINT SUGGESTION: '{generated_hint}'")
                    print("=========================================")

                    show_hint(parse_bounds(bounds), generated_hint)

                    while True:
                        feedback = input("Is this hint correct? (yes/no): ").strip().lower()
                        if feedback in ['yes', 'no']:
                            break
                        print("Invalid input. Please enter 'yes' or 'no'.")

                    if feedback == "yes":
                        correct_response = generated_hint
                        reward = 1
                    else:
                        correct_response = input("Please provide the correct hint: ").strip()
                        reward = -1
                        
                        # --- CHANGE: Display user-provided hint in terminal and as overlay ---
                        print(f"\n--- LEARNING HINT: '{correct_response}' ---")
                        show_hint(parse_bounds(bounds), correct_response)
                        time.sleep(3) # Keep correct hint visible for confirmation
                    
                    # Store feedback for training
                    rl_agent.store_feedback(final_text_prompt, generated_hint, correct_response, reward)
                    new_feedback_count += 1 
                    
                    # Persist all feedback to disk
                    feedback_data.append({
                        "prompt": final_text_prompt, "generated_response": generated_hint,
                        "correct_response": correct_response, "reward": reward
                    })
                    save_feedback(feedback_data)
                    
                    # Check if it's time to retrain the model
                    if new_feedback_count >= TRAINING_INTERVAL:
                        print(f"\nCollected {new_feedback_count} new feedback items. Starting training...")
                        rl_agent.train()
                        new_feedback_count = 0 # Reset counter
                    else:
                        print(f"Feedback stored. Training will occur in {TRAINING_INTERVAL - new_feedback_count} more items.")

                except Exception as e:
                    print(f"Error during hint generation/feedback loop: {e}")
                
                finally:
                    processed_components_on_screen.add(component_id)

        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            print("Will attempt to reconnect after a delay.")

        print("\nWaiting for 15 seconds before next cycle...")
        time.sleep(15)

if __name__ == "__main__":
    main()

