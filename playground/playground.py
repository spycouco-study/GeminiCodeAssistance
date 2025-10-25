import keyboard
import time
def print_letters_on_space():
    lowercase_letters = []
    uppercase_letters = []
    for i in range(26):
        lowercase_letters.append(chr(ord('a') + i))
        uppercase_letters.append(chr(ord('A') + i))
    letters_with_cases = lowercase_letters + uppercase_letters
    print_sequence = letters_with_cases
    current_index = 0
    print("스페이스바를 누를 때마다 소문자 전체(a-z), 이어서 대문자 전체(A-Z)가 순서대로 출력됩니다.")
    print("마지막 항목까지 출력되면 프로그램이 자동으로 종료됩니다.")
    print("프로그램을 강제 종료하려면 'Esc' 또는 'q' 키를 누르세요.")
    print("-" * 40)
    try:
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == 'space':
                    if current_index < len(print_sequence):
                        char_to_print = print_sequence[current_index]
                        print(char_to_print)
                        if current_index == len(print_sequence) - 1:
                            print(f"\n'{char_to_print}'까지 모두 출력되었습니다. 프로그램을 종료합니다.")
                            break
                        current_index += 1
                    else:
                        print("\n모든 시퀀스가 이미 출력되었습니다. 프로그램을 종료합니다.")
                        break
                elif event.name in ['esc', 'q']:
                    print("\n프로그램을 종료합니다 (수동 종료).")
                    break
    except KeyboardInterrupt:
        print("\n프로그램이 강제로 종료되었습니다 (Ctrl+C).")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
if __name__ == "__main__":
    print_letters_on_space()