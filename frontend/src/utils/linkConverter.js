/**
 * Converts URLs in text to clickable anchor tags
 * Detects both plain-text URLs and HTML links
 */
export const convertUrlsToLinks = (text) => {
    if (!text) return [];

    // Regex pattern to match URLs (http, https, www, etc.)
    const urlPattern = /(https?:\/\/[^\s<>]+|www\.[^\s<>]+|ftp:\/\/[^\s<>]+)/g;

    const parts = [];
    let lastIndex = 0;

    // Find all URLs
    const matches = [...text.matchAll(urlPattern)];

    if (matches.length === 0) {
        // No URLs found, return text as is
        return [{ type: 'text', content: text }];
    }

    matches.forEach((match) => {
        const matchStart = match.index;
        const matchEnd = match.index + match[0].length;
        const url = match[0];

        // Add text before URL
        if (matchStart > lastIndex) {
            parts.push({ type: 'text', content: text.slice(lastIndex, matchStart) });
        }

        // Add URL as link
        let fullUrl = url;
        if (!fullUrl.startsWith('http://') && !fullUrl.startsWith('https://') && !fullUrl.startsWith('ftp://')) {
            fullUrl = 'https://' + fullUrl;
        }

        parts.push({
            type: 'link',
            content: url,
            href: fullUrl
        });

        lastIndex = matchEnd;
    });

    // Add remaining text
    if (lastIndex < text.length) {
        parts.push({ type: 'text', content: text.slice(lastIndex) });
    }

    return parts;
};

/**
 * React component to render text with clickable links
 */
export const TextWithLinks = ({ text }) => {
    const parts = convertUrlsToLinks(text);

    return (
        <>
            {parts.map((part, idx) => {
                if (part.type === 'link') {
                    return (
                        <a
                            key={idx}
                            href={part.href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 underline hover:underline-offset-1 break-all"
                            title={part.href}
                        >
                            {part.content}
                        </a>
                    );
                }
                return <span key={idx}>{part.content}</span>;
            })}
        </>
    );
};
