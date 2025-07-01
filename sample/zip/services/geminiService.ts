
import { GoogleGenAI } from "@google/genai";
import { TreasureResult, SandboxSettings } from '../types';
import { Logger } from './logger';
import { CANVAS_RESOLUTION } from '../hooks/useSandboxSimulation';

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  Logger.error("API_KEY environment variable not set. Gemini API features will fail.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY! });

export const findTreasure = async (x: number, y: number, heightMap: Float32Array, settings: SandboxSettings): Promise<TreasureResult> => {
  if (!API_KEY) {
    return {
      found: false,
      item: '',
      description: 'Treasure hunting is disabled. The API Key is not configured.'
    }
  }

  // To avoid calling the API on every click, let's add a random chance.
  // The user should not find treasure every time.
  if (Math.random() > 0.15) { // 15% chance to actually ask the AI
      return { found: false, item: '', description: '' };
  }

  const digHeight = heightMap[Math.floor(y) * CANVAS_RESOLUTION + Math.floor(x)];
  const isUnderwater = digHeight < settings.seaLevel;

  // Let's get some context from the heightmap
  let highestPoint = 0;
  let lowestPoint = 255;
  let waterArea = 0;
  for (let i = 0; i < heightMap.length; i++) {
    const h = heightMap[i];
    if (h > highestPoint) highestPoint = h;
    if (h < lowestPoint) lowestPoint = h;
    if (h < settings.seaLevel) waterArea++;
  }
  const waterPercentage = (waterArea / heightMap.length) * 100;

  const prompt = `
    You are the Treasure Master for an AR sandbox game.
    A player is digging for treasure on a virtual island map.
    Based on the following information, decide if they find something interesting.
    Be creative! They could find valuable treasure, ancient artifacts, junk, or just a funny message.
    Not every dig should yield treasure. Make it rare and exciting.

    Digging location:
    - Coordinates: (x=${Math.round(x)}, y=${Math.round(y)}) on a ${CANVAS_RESOLUTION}x${CANVAS_RESOLUTION} map.
    - Elevation: ${Math.round(digHeight)} (out of 255).
    - Is it underwater? ${isUnderwater ? 'Yes' : 'No'}.

    Island context:
    - Sea Level is set at: ${settings.seaLevel}.
    - Highest peak on the island: ${Math.round(highestPoint)}.
    - Deepest point on the island: ${Math.round(lowestPoint)}.
    - Percentage of map covered by water: ${waterPercentage.toFixed(1)}%.

    Rules:
    - Finding something should be uncommon. If nothing is found, set "found" to false.
    - Treasures are more likely to be found at interesting locations: high peaks, deep underwater caves, shorelines, or exactly at sea level.
    - Make the item and description fit the location. A rusty anchor underwater, a pirate's spyglass on a peak, a message in a bottle on the beach.

    Respond with a JSON object with this exact structure:
    {
      "found": boolean,
      "item": string,
      "description": string
    }
    If "found" is false, "item" and "description" should be empty strings.
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-04-17",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      }
    });

    let jsonStr = response.text.trim();
    const fenceRegex = /^```(\w*)?\s*\n?(.*?)\n?\s*```$/s;
    const match = jsonStr.match(fenceRegex);
    if (match && match[2]) {
      jsonStr = match[2].trim();
    }
    
    const result = JSON.parse(jsonStr);

    if (typeof result.found === 'boolean' && typeof result.item === 'string' && typeof result.description === 'string') {
        Logger.info(`Treasure hunt result: ${result.found ? 'Found ' + result.item : 'Nothing found'}.`);
        return result;
    }
    throw new Error('Invalid JSON structure from Gemini API');

  } catch (error) {
    Logger.error('Error calling Gemini API for treasure:', error);
    return {
      found: false,
      item: '',
      description: 'The Treasure Master is sleeping... try again later.'
    };
  }
};
