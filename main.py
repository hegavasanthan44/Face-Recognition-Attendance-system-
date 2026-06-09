#!/usr/bin/env python3
import os
import sys
import cv2
from face_recognition_module import FaceRecognitionModule
from attendance_manager import AttendanceManager
from report_generator import ReportGenerator

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def print_header(title):
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60 + "\n")

def main_menu():
    clear_screen()
    print_header("FACE RECOGNITION ATTENDANCE SYSTEM")

    menu_options = [
        "1. Register New Person",
        "2. Mark Attendance (Auto)",
        "3. View Attendance History",
        "4. View Statistics Dashboard",
        "5. Generate Excel Report",
        "6. Test Face Detection",
        "7. Exit"
    ]

    for option in menu_options:
        print(f"  {option}")

    print("\n" + "-"*60)
    choice = input("Select an option (1-7): ").strip()
    return choice

def register_person():
    print_header("REGISTER NEW PERSON")

    face_module = FaceRecognitionModule()
    attendance_manager = AttendanceManager()

    name = input("Enter person's name: ").strip()
    if not name:
        print("❌ Invalid name!")
        input("Press Enter to continue...")
        return

    email = input("Enter email (optional): ").strip()

    success, message = attendance_manager.register_user(name, email)
    if not success:
        print(f"❌ {message}")
        input("Press Enter to continue...")
        return

    print(f"✓ {message}")
    print("\nNow capturing face samples...")

    if face_module.capture_face(name, num_samples=3):
        print(f"✓ Face registration completed for {name}!")
    else:
        print(f"❌ Face registration cancelled")

    input("Press Enter to continue...")

def mark_attendance():
    print_header("MARK ATTENDANCE - AUTO MODE")
    print("Camera is opening. Stand in front to mark attendance.")
    print("Attendance will be marked automatically when face is recognized.\n")

    face_module = FaceRecognitionModule()
    attendance_manager = AttendanceManager()
    report_generator = ReportGenerator()

    def on_attendance_marked(name):
        success, message = attendance_manager.mark_attendance(name)
        if success:
            print(f"✓ {message}")
        else:
            print(f"⚠ {message}")

    face_module.detect_and_mark_attendance(on_attendance_marked)

    print("\n" + "-"*60)
    print("Generating Excel report...")
    try:
        filepath = report_generator.export_attendance_to_excel()
        print(f"✓ Report generated: {filepath}")
    except Exception as e:
        print(f"⚠ Could not auto-generate report: {str(e)}")

    input("Press Enter to continue...")

def view_attendance_history():
    print_header("VIEW ATTENDANCE HISTORY")

    attendance_manager = AttendanceManager()
    users = attendance_manager.get_all_users()

    if not users:
        print("No registered users found.")
        input("Press Enter to continue...")
        return

    print("Registered Users:")
    for idx, (user_id, name) in enumerate(users, 1):
        print(f"  {idx}. {name}")

    print("-"*60)
    try:
        choice = int(input("Select user (number): ")) - 1
        if 0 <= choice < len(users):
            selected_user = users[choice][1]
            records = attendance_manager.get_user_attendance_history(selected_user, days=30)

            print(f"\nAttendance History for {selected_user} (Last 30 days):")
            print("-"*60)
            print(f"{'Date & Time':<25} {'Status':<15}")
            print("-"*60)

            if records:
                for record in records:
                    date_time = record[1][:16]
                    status = record[2]
                    print(f"{date_time:<25} {status:<15}")
            else:
                print("No attendance records found.")

            print("-"*60)
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")

    input("Press Enter to continue...")

def view_statistics():
    print_header("ATTENDANCE STATISTICS DASHBOARD")

    report_generator = ReportGenerator()
    report_generator.generate_analytics_report()

    input("Press Enter to continue...")

def generate_report():
    print_header("GENERATE EXCEL REPORT")

    report_generator = ReportGenerator()

    try:
        filepath = report_generator.export_attendance_to_excel()
        print(f"✓ Report generated successfully!")
        print(f"📄 Saved to: {filepath}")
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")

    input("Press Enter to continue...")

def test_face_recognition():
    print_header("TEST FACE RECOGNITION")
    print("This will help debug if face detection is working.\n")

    face_module = FaceRecognitionModule()

    print(f"Registered faces: {len(face_module.known_face_names)}")
    if face_module.known_face_names:
        for i, name in enumerate(set(face_module.known_face_names)):
            print(f"  - {name}")
    else:
        print("  (No registered faces yet)\n")

    print("Opening camera to test face detection...")
    print("Press 'Q' to quit\n")

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_locations, face_names = face_module.recognize_face(frame)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.putText(frame, f"Faces detected: {len(face_locations)} | Press 'Q' to quit",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Face Detection Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nTest completed. Press Enter to continue...")
    input()


def main():
    while True:
        choice = main_menu()

        if choice == "1":
            register_person()
        elif choice == "2":
            mark_attendance()
        elif choice == "3":
            view_attendance_history()
        elif choice == "4":
            view_statistics()
        elif choice == "5":
            generate_report()
        elif choice == "6":
            test_face_recognition()
        elif choice == "7":
            print("\n✓ Thank you for using Face Recognition Attendance System!")
            print("Goodbye!\n")
            sys.exit(0)
        else:
            print("❌ Invalid option! Please select 1-7.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
