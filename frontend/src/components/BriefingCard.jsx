import React, { useState } from 'react';
import EmailCard from './EmailCard';

export default function BriefingCard({ briefingData, onViewDetails, onResponse }) {
    const [showSummary, setShowSummary] = useState(true);
    
    const emails = briefingData.emails || [];
    const totalCount = briefingData.total_count || emails.length;

    return (
        <div className="space-y-4 animate-fade-in w-full">
            {/* Overall Summary Panel */}
            {showSummary && (
                <div className="bg-gradient-to-r from-blue-900/40 to-purple-900/40 border border-blue-700/50 rounded-lg p-4 backdrop-blur">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-white">📧 Summary</h3>
                        <button
                            onClick={() => setShowSummary(false)}
                            className="text-gray-400 hover:text-white text-sm"
                        >
                            ✕
                        </button>
                    </div>
                    <p className="text-gray-300 text-sm mb-3">
                        {briefingData.content}
                    </p>
                    <div className="flex gap-2 text-xs">
                        <span className="bg-blue-600/50 text-blue-200 px-2 py-1 rounded">
                            {totalCount} unread email{totalCount !== 1 ? 's' : ''}
                        </span>
                        <span className="bg-purple-600/50 text-purple-200 px-2 py-1 rounded">
                            All inbox
                        </span>
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-1">
                    📬 All Unread Emails ({totalCount})
                </h3>
                <p className="text-gray-400 text-sm">
                    Here are all your unread emails. Click "View Details" to see the full content or "Response" to generate a reply.
                </p>
            </div>

            {/* Email Cards */}
            <div className="space-y-3">
                {emails.length === 0 ? (
                    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 text-center">
                        <p className="text-gray-400">No unread emails</p>
                    </div>
                ) : (
                    emails.map((email, idx) => (
                        <EmailCard
                            key={email.email_id}
                            email={email}
                            onViewDetails={onViewDetails}
                            onResponse={onResponse}
                            index={idx + 1}
                            total={totalCount}
                        />
                    ))
                )}
            </div>
        </div>
    );
}
