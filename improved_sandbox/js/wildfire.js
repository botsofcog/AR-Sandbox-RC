// wildfire.js - Wildfire simulation module

export default class Wildfire {
  constructor(options = {}) {
    // Configuration with defaults
    this.cols = options.cols || 100;
    this.rows = options.rows || 75;
    this.maxFire = options.maxFire || 100;
    this.spreadRate = options.spreadRate || 0.02;
    this.igniteRate = options.igniteRate || 0.005;
    this.decayRate = options.decayRate || 0.5;
    this.fireMap = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
  }

  igniteRandom() {
    if (Math.random() < this.igniteRate) {
      const x = Math.floor(Math.random() * this.cols);
      const y = Math.floor(Math.random() * this.rows);
      this.fireMap[y][x] = this.maxFire * 0.5;
    }
  }

  spread() {
    const newMap = this.fireMap.map(row => row.slice());
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const f = this.fireMap[y][x];
        if (f > 0) {
          // Decay
          newMap[y][x] = Math.max(0, f - this.decayRate);
          // Spread
          const neighbors = [[1,0],[-1,0],[0,1],[0,-1]];
          neighbors.forEach(([dx,dy]) => {
            const nx = x + dx, ny = y + dy;
            if (nx >= 0 && nx < this.cols && ny >= 0 && ny < this.rows) {
              if (Math.random() < this.spreadRate * (f/this.maxFire)) {
                newMap[ny][nx] = Math.min(this.maxFire, newMap[ny][nx] + f * 0.3);
              }
            }
          });
        }
      }
    }
    this.fireMap = newMap;
  }

  extinguish(px, py, radius = 30, cellW, cellH) {
    const cx = Math.floor(px / cellW);
    const cy = Math.floor(py / cellH);
    const r = Math.ceil(radius / Math.min(cellW, cellH));
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        const nx = cx + dx, ny = cy + dy;
        if (nx >= 0 && nx < this.cols && ny >= 0 && ny < this.rows) {
          if (Math.hypot(dx, dy) <= r) {
            this.fireMap[ny][nx] = Math.max(0, this.fireMap[ny][nx] - (this.maxFire * 0.1));
          }
        }
      }
    }
  }

  render(ctx, cellW, cellH) {
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const f = this.fireMap[y][x];
        if (f > 0) {
          const alpha = Math.min(f / this.maxFire, 1) * 0.6;
          ctx.fillStyle = `rgba(255,69,0,${alpha})`;
          ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
        }
      }
    }
  }

  step(ctx, cellW, cellH) {
    this.igniteRandom();
    this.spread();
    this.render(ctx, cellW, cellH);
  }
}
