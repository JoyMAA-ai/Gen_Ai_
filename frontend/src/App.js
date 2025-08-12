import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [dreamText, setDreamText] = useState("");
  const [formatType, setFormatType] = useState("video");
  const [includeAudio, setIncludeAudio] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [sessionId] = useState(() => Date.now().toString());

  const generateDreamContent = async () => {
    if (!dreamText.trim()) return;
    
    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/generate-dream`, {
        dream_text: dreamText,
        format_type: formatType,
        include_audio: includeAudio,
        session_id: sessionId
      });
      
      setGeneratedContent(response.data);
    } catch (error) {
      console.error("Error generating dream content:", error);
      alert("Failed to generate content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const resetForm = () => {
    setDreamText("");
    setGeneratedContent(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4 bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">
            Dream Teller
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Transform your dreams into captivating videos and podcasts using AI
          </p>
        </div>

        {!generatedContent ? (
          /* Input Form */
          <div className="max-w-2xl mx-auto">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
              <h2 className="text-2xl font-semibold text-white mb-6 text-center">
                Describe Your Dream
              </h2>
              
              {/* Dream Text Input */}
              <div className="mb-6">
                <textarea
                  value={dreamText}
                  onChange={(e) => setDreamText(e.target.value)}
                  placeholder="Share your dream in as much detail as you can remember... What did you see? How did you feel? What happened?"
                  className="w-full h-40 p-4 rounded-xl bg-white/10 border border-white/30 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent"
                />
                <div className="text-right text-sm text-gray-400 mt-2">
                  {dreamText.length} characters
                </div>
              </div>

              {/* Format Selection */}
              <div className="mb-6">
                <label className="block text-white font-medium mb-3">
                  Choose Format
                </label>
                <div className="flex gap-4">
                  <button
                    onClick={() => setFormatType("video")}
                    className={`flex-1 p-4 rounded-xl border-2 transition-all ${
                      formatType === "video"
                        ? "border-purple-400 bg-purple-400/20 text-white"
                        : "border-white/30 bg-white/5 text-gray-300 hover:border-purple-400/50"
                    }`}
                  >
                    <div className="text-2xl mb-2">🎬</div>
                    <div className="font-medium">Video</div>
                    <div className="text-sm opacity-75">Visual storytelling</div>
                  </button>
                  <button
                    onClick={() => setFormatType("podcast")}
                    className={`flex-1 p-4 rounded-xl border-2 transition-all ${
                      formatType === "podcast"
                        ? "border-purple-400 bg-purple-400/20 text-white"
                        : "border-white/30 bg-white/5 text-gray-300 hover:border-purple-400/50"
                    }`}
                  >
                    <div className="text-2xl mb-2">🎙️</div>
                    <div className="font-medium">Podcast</div>
                    <div className="text-sm opacity-75">Audio narration</div>
                  </button>
                </div>
              </div>

              {/* Audio Option */}
              {formatType === "video" && (
                <div className="mb-6">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeAudio}
                      onChange={(e) => setIncludeAudio(e.target.checked)}
                      className="w-5 h-5 rounded border-white/30 bg-white/10 text-purple-400 focus:ring-purple-400"
                    />
                    <span className="text-white">Include narration audio</span>
                  </label>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={generateDreamContent}
                disabled={!dreamText.trim() || isGenerating}
                className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Generating Your Dream...
                  </>
                ) : (
                  <>
                    <span>✨</span>
                    Generate {formatType === "video" ? "Video" : "Podcast"}
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* Results Display */
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">
                  Your Dream Story
                </h2>
                <div className="flex items-center justify-center gap-2 text-green-400">
                  <span>✅</span>
                  <span>Generated successfully!</span>
                </div>
              </div>

              {/* Generated Story */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-white mb-4">Story</h3>
                <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                  <p className="text-gray-200 leading-relaxed">
                    {generatedContent.generated_story}
                  </p>
                </div>
              </div>

              {/* Media Display */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Generated {formatType === "video" ? "Video" : "Podcast"}
                </h3>
                <div className="bg-white/5 rounded-xl p-8 border border-white/10 text-center">
                  {formatType === "video" ? (
                    <div>
                      <div className="text-6xl mb-4">🎬</div>
                      <p className="text-gray-300 mb-4">
                        Video generation complete! (Demo mode)
                      </p>
                      <div className="text-sm text-gray-400">
                        Video URL: {generatedContent.video_url}
                      </div>
                      {generatedContent.audio_url && (
                        <div className="text-sm text-gray-400 mt-2">
                          Audio URL: {generatedContent.audio_url}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>
                      <div className="text-6xl mb-4">🎙️</div>
                      <p className="text-gray-300 mb-4">
                        Podcast generation complete! (Demo mode)
                      </p>
                      <div className="text-sm text-gray-400">
                        Audio URL: {generatedContent.audio_url}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 justify-center">
                <button
                  onClick={resetForm}
                  className="px-6 py-3 bg-white/10 text-white border border-white/30 rounded-xl hover:bg-white/20 transition-all"
                >
                  Create Another Dream
                </button>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(generatedContent.generated_story);
                    alert("Story copied to clipboard!");
                  }}
                  className="px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition-all"
                >
                  Copy Story
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-400">
          <p>Powered by AI • Transform your dreams into stories</p>
        </div>
      </div>
    </div>
  );
}

export default App;