import { useState } from 'react';
import { Mic, Send } from 'lucide-react';

const ChatInterface = () => {
  const [message, setMessage] = useState('');

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4">
        <h1 className="text-2xl md:text-3xl font-bold text-white text-center">
          What's on your mind?
        </h1>
      </div>

      <div className="w-full px-4 pb-4 md:pb-6">
        <div className="max-w-3xl mx-auto">
          <div className="bg-gray-800 rounded-2xl p-3 md:p-4 shadow-lg">
            <div className="flex items-center space-x-3">
              <input
                type="text"
                placeholder="Type anything..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm md:text-base"
              />
              
              <button
                className="p-2 rounded-xl bg-blue-600 text-white hover:bg-blue-500 transition-colors flex items-center justify-center"
                title={message ? "Send message" : "Voice input"}
              >
                {message ? (
                  <Send size={18} className="transition-transform hover:translate-x-0.5" />
                ) : (
                  <Mic size={18} className="transition-transform hover:scale-110" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;