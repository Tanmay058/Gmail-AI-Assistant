import React, { useState, useRef, useEffect } from 'react';
import BriefingCard from './BriefingCard';
import EmailDetailModal from './EmailDetailModal';
import ReplyModal from './ReplyModal';

// Mock or Real API Endpoint
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function ChatArea() {
  const [messages, setMessages] = useState([
    { role: 'ai', type: 'text', content: "Hello! I'm your Gmail Assistant. Ask me about your unread emails or general questions." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Modal States
  const [viewingEmail, setViewingEmail] = useState(null);
  const [replyingEmail, setReplyingEmail] = useState(null);

  const endRef = useRef(null);

  const scrollToBottom = () => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', type: 'text', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content })
      });
      const data = await response.json();

      // Data expected: { type: 'text'|'briefing', content: '...', emails: []? }
      const aiMsg = {
        role: 'ai',
        type: data.type || 'text',
        content: data.content,
        data: data
      };
      setMessages(prev => [...prev, aiMsg]);

    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', type: 'error', content: "Sorry, something went wrong connecting to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  const sendReply = async (emailId, body) => {
    try {
      const response = await fetch(`${API_URL}/email/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_id: emailId, reply_body: body })
      });

      if (!response.ok) throw new Error("Send failed");

      alert("✅ Reply Sent Successfully!");
      return true;
    } catch (e) {
      alert("❌ Failed to send reply. Please check your connection.");
      throw e;
    }
  }

  return (
    <div className="h-full flex flex-col relative">

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>

            {/* User Message */}
            {msg.role === 'user' && (
              <div className="bg-blue-600 text-white px-4 py-2 rounded-2xl rounded-tr-sm max-w-[80%] text-sm">
                {msg.content}
              </div>
            )}

            {/* AI Text Message */}
            {msg.role === 'ai' && msg.type === 'text' && (
              <div className="bg-gray-800 text-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[80%] text-sm border border-gray-700">
                {msg.content}
              </div>
            )}

            {/* AI Error Message */}
            {msg.role === 'ai' && msg.type === 'error' && (
              <div className="bg-red-900/20 text-red-400 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[80%] text-sm border border-red-900">
                {msg.content}
              </div>
            )}

            {/* AI Briefing Card */}
            {msg.role === 'ai' && msg.type === 'briefing' && (
              <div className="w-full max-w-xl">
                <BriefingCard
                  briefingData={msg.data}
                  onViewDetails={setViewingEmail}
                  onResponse={setReplyingEmail}
                />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-gray-400 px-4 py-2 rounded-2xl rounded-tl-sm text-xs animate-pulse">
              Thinking...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-800 bg-gray-900/50 backdrop-blur">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask your assistant..."
            className="flex-1 bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder-gray-500"
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 rounded-lg font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </div>

      {/* Modals */}
      {viewingEmail && (
        <EmailDetailModal
          email={viewingEmail}
          onClose={() => setViewingEmail(null)}
        />
      )}

      {replyingEmail && (
        <ReplyModal
          email={replyingEmail}
          onClose={() => setReplyingEmail(null)}
          onSend={sendReply}
        />
      )}

    </div>
  );
}
