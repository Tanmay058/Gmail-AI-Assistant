import React from 'react';
import { TextWithLinks } from '../utils/linkConverter.jsx';

export default function EmailCard({ email, onViewDetails, onResponse, index, total }) {
  // Extract sender name from email address
  const getSenderName = (fromString) => {
    if (!fromString) return "Unknown";
    // Extract name before <email@domain.com>
    const match = fromString.match(/^([^<]+)</);
    return match ? match[1].trim() : fromString.split('<')[0].trim();
  };

  const senderName = getSenderName(email.from);
  const senderEmail = email.from || "";

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:bg-gray-750 transition-all hover:border-gray-600">

      {/* Header with sender and email counter */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-gray-100 text-sm">
              {senderName}
            </h4>
            {index && total && (
              <span className="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded">
                {index}/{total}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 truncate">
            {senderEmail}
          </p>
        </div>
      </div>

      {/* Subject */}
      <div className="mb-3">
        <p className="text-sm font-medium text-gray-200 line-clamp-2">
          {email.subject || "(No subject)"}
        </p>
      </div>

      {/* Summary with clickable links */}
      <div className="bg-gray-900/50 border border-gray-700/50 rounded p-3 mb-4">
        <p className="text-gray-300 text-sm leading-relaxed line-clamp-4">
          <TextWithLinks text={(email.summary || "No summary available.").replace(/<[^>]*>|&lt;[^&gt;]*&gt;/gi, ' ').trim()} />
        </p>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => onResponse(email)}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-2.5 rounded-md transition-colors flex items-center justify-center gap-1"
        >
          💬 Response
        </button>
        <button
          onClick={() => onViewDetails(email)}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-gray-200 text-xs font-medium py-2.5 rounded-md transition-colors flex items-center justify-center gap-1"
        >
          👁️ View Details
        </button>
      </div>
    </div>
  );
}
