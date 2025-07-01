using System;
using System.IO;
using UnityEngine;

namespace Sandbox.Scripts.ServerClient
{
    [Serializable]
    public class SandboxClientConfig
    {
        public string Ip;
        public string Port;
        public string Endpoint;
        public int HttpMethod;

        private static string GetConfigPath()
        {
            return Path.Combine(Application.persistentDataPath, "SandboxClientConfig.json");
        }

        public static void SaveConfig(SandboxClientConfig config)
        {
            string json = JsonUtility.ToJson(config);
            File.WriteAllText(GetConfigPath(), json);
        }

        public static SandboxClientConfig LoadConfig()
        {
            string path = GetConfigPath();
            if (File.Exists(path))
            {
                string json = File.ReadAllText(path);
                return JsonUtility.FromJson<SandboxClientConfig>(json);
            }
            return new SandboxClientConfig(); // Return default config if file doesn't exist
        }
    }
}