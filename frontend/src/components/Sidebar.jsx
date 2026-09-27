import React, { useState, useEffect } from 'react';
import { TextWithLinks } from '../utils/linkConverter.jsx';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Sidebar() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);

  // Fetch unread emails on component mount
  useEffect(() => {
    fetchUnreadEmails();
  }, []);

  const fetchUnreadEmails = async () => {
    setLoading(true);
    try {
      // Call the dedicated endpoint for all unread emails
      const response = await fetch(`${API_URL}/emails/unread`, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) {
        throw new Error("Failed to fetch emails");
      }

      const data = await response.json();

      if (data.emails) {
        setEmails(data.emails);
      }
    } catch (error) {
      console.error("Error fetching emails:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    // Simple time formatter - you can enhance this
    const now = new Date();
    const emailTime = new Date(timestamp);
    const diffHours = Math.floor((now - emailTime) / (1000 * 60 * 60));

    if (diffHours < 1) return "Now";
    if (diffHours < 24) return `${diffHours}h ago`;
    return "Yesterday";
  };

  const truncateText = (text, length = 40) => {
    return text.length > length ? text.substring(0, length) + "..." : text;
  };

  return (
    <div className="h-full flex flex-col p-4 text-white">

      {/* App Title */}
      <h1 className="text-xl font-semibold mb-4">
        Gmail AI Assistant
      </h1>

      {/* Refresh Button */}
      <button
        onClick={fetchUnreadEmails}
        disabled={loading}
        className="mb-4 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition disabled:opacity-50"
      >
        {loading ? "Loading..." : "Check Unread Emails"}
      </button>

      {/* Email Threads */}
      <div className="flex-1 overflow-y-auto space-y-2">

        {emails.length === 0 ? (
          <div className="p-3 text-gray-400 text-sm">
            {loading ? "Loading emails..." : "No unread emails"}
          </div>
        ) : (
          emails.map((email, index) => (
            <div
              key={index}
              onClick={() => setSelectedEmail(email)}
              className="p-3 rounded-lg bg-gray-800 cursor-pointer hover:bg-gray-700 transition"
            >
              <div className="flex justify-between items-center">
                <p className="font-medium truncate text-sm">
                  {email.from ? email.from.split("<")[0].trim() : "Unknown"}
                </p>
                <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
                  {formatTime(email.timestamp || new Date())}
                </span>
              </div>
              <p className="text-sm text-gray-300 truncate mt-1">
                {truncateText(email.subject || "No subject")}
              </p>
            </div>
          ))
        )}

      </div>

      {/* Email Detail Modal */}
      {selectedEmail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">

            {/* Header */}
            <div className="bg-gray-800/50 border-b border-gray-700 px-6 py-4 flex justify-between items-start">
              <div className="flex-1">
                <h2 className="text-xl font-bold text-white mb-1">
                  {selectedEmail.subject || "(No subject)"}
                </h2>
                <p className="text-sm text-gray-400">
                  From: {selectedEmail.from || "Unknown"}
                </p>
              </div>
              <button
                onClick={() => setSelectedEmail(null)}
                className="text-gray-400 hover:text-white text-2xl font-light"
              >
                ✕
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="px-6 py-6">

                {/* Summary Section */}
                {selectedEmail.summary && (
                  <div className="mb-6 pb-6 border-b border-gray-700">
                    <h3 className="text-sm font-semibold text-blue-400 mb-3 uppercase tracking-wide">
                      📋 Summary
                    </h3>
                    <div className="bg-blue-900/20 border border-blue-700/30 rounded-lg p-4 text-gray-200 text-sm leading-relaxed">
                      {selectedEmail.summary}
                    </div>
                  </div>
                )}

                {/* Full Email Body */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">
                    📧 Full Email
                  </h3>
                  <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 text-gray-300 text-sm leading-relaxed overflow-auto max-h-[60vh]">
                    <div dangerouslySetInnerHTML={{ __html: selectedEmail.body || "No content available" }} />
                  </div>
                </div>

              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-800/50 border-t border-gray-700 px-6 py-4 flex justify-end gap-3">
              <button
                onClick={() => setSelectedEmail(null)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition text-sm font-medium"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  )
}
