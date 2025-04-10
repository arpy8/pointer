const canvas = document.getElementById("joystickCanvas");
const ctx = canvas.getContext("2d");
const pi = Math.PI;

var gradient;
function fixDpiResizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.width = canvas.offsetWidth * dpr;
  canvas.height = canvas.offsetHeight * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener("resize", fixDpiResizeCanvas);
fixDpiResizeCanvas();

var positions = {
  fixedX: undefined,
  fixedY: undefined,
  innerX: undefined,
  innerY: undefined,
};

var angle = undefined;

function touchStart(x, y) {
  if (positions.fixedX || positions.fixedY) return;
  positions.fixedX = positions.innerX = x;
  positions.fixedY = positions.innerY = y;
}

function touchMove(x, y) {
  if (!(positions.fixedX || positions.fixedY)) return;

  positions.innerX = x;
  positions.innerY = y;

  angle = Math.atan2(
    positions.innerY - positions.fixedY,
    positions.innerX - positions.fixedX
  );

  const distanceSquared = (x - positions.fixedX) ** 2 + (y - positions.fixedY) ** 2;
  const joystickRadiusSquared = 1000;

  if (distanceSquared > joystickRadiusSquared) {
    const distance = Math.sqrt(distanceSquared);
    positions.innerX = ((x - positions.fixedX) / distance) * 45 + positions.fixedX;
    positions.innerY = ((y - positions.fixedY) / distance) * 45 + positions.fixedY;
  }
}

function touchEndOrCancel() {
  positions.fixedX =
    positions.fixedY =
    positions.innerX =
    positions.innerY =
    angle =
      undefined;
}

function resetJoystick() {
  positions.fixedX =
    positions.fixedY =
    positions.innerX =
    positions.innerY =
    angle =
      undefined;
}

canvas.addEventListener("touchstart", (e) =>
  touchStart(e.touches[0].clientX, e.touches[0].clientY)
);
canvas.addEventListener("touchmove", (e) =>
  touchMove(e.touches[0].clientX, e.touches[0].clientY)
);
canvas.addEventListener("touchend", touchEndOrCancel);
canvas.addEventListener("touchcancel", touchEndOrCancel);

canvas.addEventListener("mousedown", (e) => touchStart(e.offsetX, e.offsetY));
canvas.addEventListener("mousemove", (e) => touchMove(e.offsetX, e.offsetY));
canvas.addEventListener("mouseup", touchEndOrCancel);

canvas.addEventListener("mouseleave", resetJoystick); // Reset on mouse leave
canvas.addEventListener("touchleave", resetJoystick); // Reset on touch leave

function renderLoop() {
  requestAnimationFrame(renderLoop);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!(positions.fixedX || positions.fixedY)) return;

  ctx.beginPath();
  ctx.fillStyle = "#fff4";
  ctx.arc(positions.fixedX, positions.fixedY, 40, 0, 2 * pi);
  ctx.fill();
  ctx.closePath();

  ctx.beginPath();
  ctx.fillStyle = "#fff8";
  ctx.arc(positions.innerX, positions.innerY, 10, 0, 2 * pi);
  ctx.fill();
  ctx.closePath();
}

renderLoop();