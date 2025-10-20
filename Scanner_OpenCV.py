import cv2
from warnings import filterwarnings

filterwarnings(action='ignore')

def qr_code_scanner():
    # Open the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    detector = cv2.QRCodeDetector()  # OpenCV QR detector

    # Loop until a QR code is detected
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Detect and decode QR
        data, points, _ = detector.detectAndDecode(frame)

        # Show camera
        cv2.imshow('QR Code Scanner', frame)

        # If QR is found
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return data  #  Same behavior as your obj.data.decode()

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


if __name__ == "__main__":
    text = qr_code_scanner()
    print(text)

