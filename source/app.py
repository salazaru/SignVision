import time
import edgeiq
import RPi.GPIO as GPIO
import cv2
"""
Use object detection to detect human faces in the frame in realtime.
 
To change the computer vision model, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_model.html
 
To change the engine and accelerator, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html
"""
 
 
def main():
    facial_detector = edgeiq.ObjectDetection(
            "alwaysai/res10_300x300_ssd_iter_140000")
    facial_detector.load(engine=edgeiq.Engine.DNN)
 
    print("Engine: {}".format(facial_detector.engine))
    print("Accelerator: {}\n".format(facial_detector.accelerator))
    print("Model:\n{}\n".format(facial_detector.model_id))
 
    fps = edgeiq.FPS()
 
    # servo trigger variables
    isFaceDetected = False
    servoPIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPIN, GPIO.OUT)
 
    try:
        with edgeiq.WebcamVideoStream(cam=0) as webcam, \
                edgeiq.Streamer() as streamer:
            # Allow webcam to warm up
            time.sleep(2.0)
            fps.start()
            p.start(2.5) # Initialization
            p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
 
            # loop detection
            while True:
                frame = webcam.read()
                # detect human faces
                results = facial_detector.detect_objects(
                        frame, confidence_level=.5)
                frame = edgeiq.markup_image(
                        frame, results.predictions, show_labels=False)
 
                # Generate text to display on streamer
                text = ["Model: {}".format(facial_detector.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration))
                text.append("Faces:")
 
                for prediction in results.predictions:
                    text.append("{:2.2f}%".format(prediction.confidence * 100))   
 
                streamer.send_data(frame, text)
                if(text[-1] > 95 and isFaceDetected == False):
                    # servo code
                    p.ChangeDutyCycle(13)
                    p.stop()
                    isFaceDetected = True
 
                fps.update()
 
                if streamer.check_exit():
                    break
 
    finally:
        # stop fps counter and display information
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.compute_fps()))
 
        print("Program Ending")
        GPIO.cleanup()
 
if __name__ == "__main__":
    main()