import React from 'react';
import { TextWithLinks } from '../utils/linkConverter.jsx';

export default function EmailDetailModal({ email, onClose }) {
    if (!email) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">

                {/* Header */}
                <div className="p-5 border-b border-gray-800 flex justify-between items-center">
                    <div>
                        <h3 className="text-lg font-bold text-white max-w-md truncate">{email.subject}</h3>
                        <p className="text-sm text-gray-400">From: {email.from}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        ✕
                    </button>
                </div>

                {/* content */}
                <div className="p-6 overflow-y-auto text-gray-300 text-sm leading-7 font-sans bg-gray-900/50">
                    <div dangerouslySetInnerHTML={{ __html: email.body }} />
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-800 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
