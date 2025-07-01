from flask import Flask, render_template
from flask_sock import Sock
import cv2, torch, numpy as np
from midas.midas_net import MidasNet
from midas.transforms import Resize

app = Flask(__name__)
sock = Sock(app)

# load MiDaS
model = MidasNet("midas/model-f6b98070.pt", non_negative=True).eval().to('cpu')
transform = Resize(384)

@sock.route('/depth_ws')
def depth_ws(ws):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret: break
        inp = transform({"image": frame})["image"]
        tensor = torch.from_numpy(inp).unsqueeze(0)
        with torch.no_grad():
            depth = model.forward(tensor).squeeze().cpu().numpy()
        dmin, dmax = depth.min(), depth.max()
        disp = ((depth-dmin)/(dmax-dmin)*255).astype(np.uint8)
        _, jpg = cv2.imencode('.jpg', disp)
        ws.send(jpg.tobytes())
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)
