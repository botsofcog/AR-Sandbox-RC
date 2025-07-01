using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using ARSandbox;
using Newtonsoft.Json;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;

namespace Sandbox.Scripts.ServerClient
{
    public class SandboxClient : MonoBehaviour
    {
        public ARSandbox.Sandbox Sandbox;
        public Shader ServerShader;
        private RenderTexture _serverRenderTexture;
        private SandboxDescriptor sandboxDescriptor;
        
        private string _sanitizedUrl;
        private bool _running= false;
        private List<string> logMessages = new List<string>();
        
        private bool ServerFrameReceived = false;
        private bool ReadyForNewFrame = true;
        private bool _configSaved = false;
        private UnityWebRequest webRequest;
        private byte[] tempImageData;
        
        //UI Elements
        public TMP_Text requestLog;
        public TMP_InputField  ipInput;
        public TMP_InputField  portInput;
        public TMP_InputField  endpointInput;
        public TMP_Dropdown httpDropdown;
        public Text startStopButtonText;
       

        private void OnEnable()
        {
            Sandbox.SetSandboxShader(ServerShader);
            Sandbox.SetShaderTexture("_FireSurfaceTex", _serverRenderTexture);
            sandboxDescriptor = Sandbox.GetSandboxDescriptor();
            LoadConfig();
        }

        public void ToggleStartStop()
        {
            if (_running)
            {
                Stop();
            }
            else
            {
                Run();
            }
        }
        private void Run()
        {
            requestLog.text = "";
            _sanitizedUrl = ParseSanitizedUrl();
            _running = true;
            _configSaved = false;
            startStopButtonText.text = "Stop";
            
            //reset
            ServerFrameReceived = false;
            ReadyForNewFrame = true;
            webRequest = null;
        }
        
        private void Stop()
        {
            _running = false;
            // Release the RenderTexture when the object is disabled
            if (_serverRenderTexture != null)
            {
                _serverRenderTexture.Release();
                Destroy(_serverRenderTexture);
                _serverRenderTexture = null;
            }
            startStopButtonText.text = "Start";
        }

        private void OnDisable()
        {
            Stop();
            // Release the RenderTexture when the object is disabled
            if (_serverRenderTexture != null)
            {
                _serverRenderTexture.Release();
                Destroy(_serverRenderTexture);
                _serverRenderTexture = null;
            }
            //reset the shader to default
            Sandbox.SetDefaultShader();
        }

        public class ImageResponse
        {
            [JsonProperty("image")]
            public string Image { get; set; }
        }
        
        private void Update()
        {
            if (!_running) return;
            
            if (ServerFrameReceived)
            {
                ServerFrameReceived = false;
                ProcessServerFrame();
            }

            if (ReadyForNewFrame)
            {
                ReadyForNewFrame = false;
                SendFramePayload(); // Start the method without waiting for it to complete
            }
            
        }

        private void SendFramePayload()
        {
            var renderTexture = Sandbox.CurrentProcessedRT;

            if (renderTexture.format != RenderTextureFormat.RHalf)
            {
                Debug.LogError("Input RenderTexture is not in RHalf format");
                Stop();
                return;
            }

            var texture2D = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RHalf, false);
            RenderTexture.active = renderTexture;
            texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
            texture2D.Apply();
            RenderTexture.active = null;

            float[] pixelData = new float[texture2D.width * texture2D.height];
            Color[] pixels = texture2D.GetPixels();
            for (int i = 0; i < pixels.Length; i++)
            {
                pixelData[i] = pixels[i].r; // Assuming RHalf stores data in the red channel
            }

            var pixelDataBytes = new byte[pixelData.Length * sizeof(float)];
            Buffer.BlockCopy(pixelData, 0, pixelDataBytes, 0, pixelDataBytes.Length);

            string url = $"{_sanitizedUrl}?width={texture2D.width}&height={texture2D.height}&minDepth={sandboxDescriptor.MinDepth}&maxDepth={sandboxDescriptor.MaxDepth}";

            UnityWebRequest webRequest = new UnityWebRequest(url, httpDropdown.options[httpDropdown.value].text);
            webRequest.uploadHandler = new UploadHandlerRaw(pixelDataBytes);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/octet-stream");

            webRequest.SendWebRequest().completed += (AsyncOperation operation) =>
            {
                if (webRequest.result == UnityWebRequest.Result.ConnectionError ||
                    webRequest.result == UnityWebRequest.Result.ProtocolError)
                {
                    UserLogError(webRequest.error);
                    Stop();
                }
                else
                {
                    string jsonResponse = webRequest.downloadHandler.text;
                    ImageResponse responseData = JsonConvert.DeserializeObject<ImageResponse>(jsonResponse);
                    if (responseData != null && !string.IsNullOrEmpty(responseData.Image))
                    {
                        UserLog(webRequest.responseCode+" - "+webRequest.result);
                        if (!_configSaved) SaveConfig(); // Save the config after the first successful request
                        tempImageData = Convert.FromBase64String(responseData.Image);
                        ServerFrameReceived = true;
                    }
                    else
                    {
                        UserLogError("Image data not found in response");
                        Stop();
                    }
                }
            };

            // Destroy the temporary Texture2D to free up memory
            Destroy(texture2D);
        }
        
        private async void ProcessServerFrame()
        {
            Texture2D tempTexture = new Texture2D(2, 2);
            tempTexture.LoadImage(tempImageData);

            if (_serverRenderTexture == null)
            {
                _serverRenderTexture = new RenderTexture(tempTexture.width, tempTexture.height, 0, RenderTextureFormat.ARGB32);
                _serverRenderTexture.Create();
            }

            RenderTexture.active = _serverRenderTexture;
            Graphics.Blit(tempTexture, _serverRenderTexture);
            RenderTexture.active = null;
            Sandbox.SetShaderTexture("_FireSurfaceTex", _serverRenderTexture);

            Destroy(tempTexture);
            ReadyForNewFrame = true;
        }

        private string ParseSanitizedUrl()
        {
            //set and remove whitespace
            string ip = ipInput.text.Replace(" ", "").Replace("\u200B","").Trim();
            string port = portInput.text.Replace(" ", "").Replace("\u200B","").Trim();
            string endpoint = endpointInput.text.Replace(" ", "").Replace("\u200B","").Trim();

            if (string.IsNullOrEmpty(ip) || string.IsNullOrEmpty(port) || string.IsNullOrEmpty(endpoint))
            {
                UserLogError("IP, Port, or Endpoint is empty");
                
                Stop();
            }
            //remove http://
            if (ip.StartsWith("http://"))
            {
                ip = ip.Substring(7);
            }
            //check if port is a number
            if (!int.TryParse(port, out _))
            {
                UserLogError("Port is not a number");
                Stop();
            }
            //remove / from endpoint
            if (endpoint.StartsWith("/"))
            {
                endpoint = endpoint.Substring(1);
            }
            // remove trailing /
            if (endpoint.EndsWith("/"))
            {
                endpoint = endpoint.Substring(0, endpoint.Length - 1);
            }
            
            return $"http://{ip}:{port}/{endpoint}";
        }
        
        private string GetTimestamp()
        {
            return DateTime.Now.ToString("HH:mm:ss");
        }

        private void AddLogMessage(string message, string color)
        {
            string timestampedMessage = $"[{GetTimestamp()}] {message}";
            if (logMessages.Count >= 12)
            {
                logMessages.RemoveAt(0);
            }
            logMessages.Add($"<color={color}>{timestampedMessage}</color>");
            UpdateLogUI();
        }

        private void UpdateLogUI()
        {
            requestLog.text = string.Join("\n", logMessages);
        }

        private void UserLog(string message)
        {
            Debug.Log(message);
            AddLogMessage(message, "white");
        }

        private void UserLogError(string message)
        {
            Debug.LogError(message);
            AddLogMessage(message, "red");
        }

        private void SaveConfig()
        {
            var config = new SandboxClientConfig
            {
                Ip = ipInput.text,
                Port = portInput.text,
                Endpoint = endpointInput.text,
                HttpMethod = httpDropdown.value
            };
            SandboxClientConfig.SaveConfig(config);
            UserLog("Config saved");
            _configSaved = true;
        }
        
        private void LoadConfig()
        {
            var config = SandboxClientConfig.LoadConfig();
            ipInput.text = config.Ip;
            portInput.text = config.Port;
            endpointInput.text = config.Endpoint;
            httpDropdown.value = config.HttpMethod;
        }

        
    }
}