// terrain.js - Advanced terrain simulation with water diffusion

export default class TerrainSimulation {
  constructor(options = {}) {
    this.cols = options.cols || 120;
    this.rows = options.rows || 90;
    this.heightMap = Array.from({ length: this.rows }, () => Array(this.cols).fill(0.5));
    this.waterMap = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
    this.velocityX = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
    this.velocityY = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
    
    this.diffusionRate = options.diffusionRate || 0.1;
    this.evaporationRate = options.evaporationRate || 0.002;
    this.gravity = options.gravity || 0.1;
    this.damping = options.damping || 0.95;
  }

  // Brush terrain modification
  modifyTerrain(px, py, radius, strength, cellW, cellH, raise = true) {
    const cx = Math.floor(px / cellW);
    const cy = Math.floor(py / cellH);
    const r = Math.ceil(radius / Math.min(cellW, cellH));
    
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        const nx = cx + dx, ny = cy + dy;
        if (nx >= 0 && nx < this.cols && ny >= 0 && ny < this.rows) {
          const dist = Math.hypot(dx, dy);
          if (dist <= r) {
            const falloff = 1 - (dist / r);
            const delta = strength * falloff * 0.01;
            if (raise) {
              this.heightMap[ny][nx] = Math.min(1, this.heightMap[ny][nx] + delta);
            } else {
              this.heightMap[ny][nx] = Math.max(0, this.heightMap[ny][nx] - delta);
            }
          }
        }
      }
    }
  }

  // Add water at position
  addWater(px, py, amount, cellW, cellH) {
    const cx = Math.floor(px / cellW);
    const cy = Math.floor(py / cellH);
    if (cx >= 0 && cx < this.cols && cy >= 0 && cy < this.rows) {
      this.waterMap[cy][cx] += amount;
    }
  }

  // Water simulation step
  simulateWater() {
    const newWater = this.waterMap.map(row => row.slice());
    const newVelX = this.velocityX.map(row => row.slice());
    const newVelY = this.velocityY.map(row => row.slice());

    for (let y = 1; y < this.rows - 1; y++) {
      for (let x = 1; x < this.cols - 1; x++) {
        if (this.waterMap[y][x] > 0.001) {
          // Calculate pressure gradients
          const heightHere = this.heightMap[y][x] + this.waterMap[y][x];
          const gradX = (this.heightMap[y][x+1] + this.waterMap[y][x+1]) - (this.heightMap[y][x-1] + this.waterMap[y][x-1]);
          const gradY = (this.heightMap[y+1][x] + this.waterMap[y+1][x]) - (this.heightMap[y-1][x] + this.waterMap[y-1][x]);

          // Update velocities
          newVelX[y][x] = (this.velocityX[y][x] - gradX * this.gravity) * this.damping;
          newVelY[y][x] = (this.velocityY[y][x] - gradY * this.gravity) * this.damping;

          // Move water based on velocity
          const flowX = newVelX[y][x] * this.waterMap[y][x] * this.diffusionRate;
          const flowY = newVelY[y][x] * this.waterMap[y][x] * this.diffusionRate;

          if (Math.abs(flowX) > 0.001) {
            const targetX = x + Math.sign(flowX);
            if (targetX >= 0 && targetX < this.cols) {
              const transfer = Math.min(Math.abs(flowX), this.waterMap[y][x] * 0.5);
              newWater[y][x] -= transfer;
              newWater[y][targetX] += transfer;
            }
          }

          if (Math.abs(flowY) > 0.001) {
            const targetY = y + Math.sign(flowY);
            if (targetY >= 0 && targetY < this.rows) {
              const transfer = Math.min(Math.abs(flowY), this.waterMap[y][x] * 0.5);
              newWater[y][x] -= transfer;
              newWater[targetY][x] += transfer;
            }
          }

          // Evaporation
          newWater[y][x] = Math.max(0, newWater[y][x] - this.evaporationRate);
        }
      }
    }

    this.waterMap = newWater;
    this.velocityX = newVelX;
    this.velocityY = newVelY;
  }

  // Render terrain with height-based coloring
  render(ctx, cellW, cellH) {
    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const height = this.heightMap[y][x];
        const water = this.waterMap[y][x];
        
        let color;
        if (water > 0.01) {
          // Water rendering
          const waterAlpha = Math.min(water * 2, 0.8);
          color = `rgba(30, 144, 255, ${waterAlpha})`;
        } else {
          // Terrain rendering based on height
          if (height < 0.2) {
            color = `rgb(139, 69, 19)`; // Brown (low)
          } else if (height < 0.4) {
            color = `rgb(160, 82, 45)`; // Saddle brown
          } else if (height < 0.6) {
            color = `rgb(210, 180, 140)`; // Tan
          } else if (height < 0.8) {
            color = `rgb(34, 139, 34)`; // Forest green
          } else {
            color = `rgb(255, 255, 255)`; // White (peaks)
          }
        }
        
        ctx.fillStyle = color;
        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
      }
    }
  }

  step(ctx, cellW, cellH) {
    this.simulateWater();
    this.render(ctx, cellW, cellH);
  }
}
