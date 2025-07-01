const ws = new WebSocket(`ws://${location.host}/depth_ws`);
const cnv = document.getElementById('depth');
const ctx = cnv.getContext('2d');

ws.binaryType = 'arraybuffer';
ws.onmessage = e => {
  const blob = new Blob([e.data], {type:'image/jpeg'});
  const img  = new Image();
  img.onload = ()=>{ ctx.drawImage(img,0,0); };
  img.src = URL.createObjectURL(blob);
};
