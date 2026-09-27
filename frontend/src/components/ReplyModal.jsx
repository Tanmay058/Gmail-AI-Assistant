import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function ReplyModal({ email, onClose, onSend }) {
    const [loading, setLoading] = useState(true);
    const [sending, setSending] = useState(false);
    const [options, setOptions] = useState([]);
    const [metadata, setMetadata] = useState(null);
    const [selectedOption, setSelectedOption] = useState(null);
    const [customBody, setCustomBody] = useState("");

    useEffect(() => {
        // Generate Options on Load
        const fetchOptions = async () => {
            try {
                const response = await fetch(`${API_URL}/email/generate-reply`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email_text: email.body,
                        sender: email.from
                    })
                });
                const data = await response.json();
                setOptions(data.options || []);
                setMetadata(data.metadata || null);
                if (data.options?.length > 0) {
                    setSelectedOption(data.options[0]);
                    setCustomBody(data.options[0].body);
                }
            } catch (error) {
                console.error("Error generating replies:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchOptions();
    }, [email]);

    const handleOptionClick = (opt) => {
        setSelectedOption(opt);
        setCustomBody(opt.body);
    }

    const handleSend = async () => {
        setSending(true);
        try {
            await onSend(email.email_id, customBody);
            // Successfully sent
            onClose();
        } catch (error) {
            console.error("Send error:", error);
            // Error is handled in onSend (alert), but we should stop loading
        } finally {
            setSending(false);
        }
    }

    if (!email) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl">

                {/* Header */}
                <div className="p-5 border-b border-gray-800">
                    <h3 className="text-lg font-bold text-white">Generate Response</h3>
                    <p className="text-sm text-gray-400 truncate">Re: {email.subject}</p>
                </div>

                <div className="flex-1 flex overflow-hidden">
                    {/* Sidebar Options */}
                    <div className="w-1/3 border-r border-gray-800 p-4 space-y-2 overflow-y-auto">

                        {/* KB Indicator */}
                        {metadata?.kb_used && (
                            <div className="mb-2 px-2 py-1 bg-green-900/40 border border-green-700/50 rounded text-xs text-green-300 flex items-center gap-1">
                                <span>✨ Using {metadata.kb_examples_found} past replies</span>
                            </div>
                        )}

                        {loading ? (
                            <div className="text-gray-500 text-sm animate-pulse">Generating AI Options...</div>
                        ) : (
                            options.map((opt, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => handleOptionClick(opt)}
                                    className={`p-3 rounded-lg cursor-pointer text-sm border ${selectedOption === opt ? 'bg-blue-900/30 border-blue-500 text-blue-200' : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-750'}`}
                                >
                                    <div className="font-semibold mb-1 text-xs uppercase tracking-wider">{opt.label}</div>
                                    <div className="line-clamp-2 opacity-70 text-xs">{opt.body}</div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Editor */}
                    <div className="flex-1 p-4 flex flex-col">
                        <textarea
                            className="flex-1 bg-gray-950 border border-gray-800 rounded-lg p-4 text-gray-300 font-mono text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                            value={customBody}
                            onChange={(e) => setCustomBody(e.target.value)}
                            placeholder="Select an option or start typing..."
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-800 flex justify-end gap-3">
                    <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white text-sm">
                        Cancel
                    </button>
                    <button
                        onClick={handleSend}
                        disabled={sending}
                        className={`px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {sending ? "Sending..." : "Send Reply"}
                    </button>
                </div>
            </div>
        </div>
    );
}
