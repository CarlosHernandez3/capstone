
import React from 'react';

interface ResultsDisplayProps {
  markdownContent: string;
}

// Simple Markdown Parser Component
const MarkdownParser: React.FC<{ content: string }> = ({ content }) => {
  const lines = content.split('\n');

  const applyInlineFormatting = (line: string) => {
    // Bold: **text**
    line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic: *text*
    line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Emoji checkmarks
    line = line.replace(/✅/g, '<span class="text-accent">✅</span>');
    line = line.replace(/❌/g, '<span class="text-danger">❌</span>');
    line = line.replace(/⚠️/g, '<span class="text-secondary">⚠️</span>');
    return { __html: line };
  };

  const elements: (JSX.Element | null)[] = [];
  let listItems: JSX.Element[] = [];

  const flushListItems = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="list-disc list-inside space-y-2 text-neutral-700 pl-4">
          {listItems}
        </ul>
      );
      listItems = [];
    }
  };

  lines.forEach((line, index) => {
    line = line.trim();

    if (line.startsWith('* ')) {
      listItems.push(<li key={index} dangerouslySetInnerHTML={applyInlineFormatting(line.substring(2))} />);
    } else {
      flushListItems(); // End of a list, if any

      if (line.startsWith('### ')) {
        elements.push(<h3 key={index} className="text-xl font-bold text-neutral-900 mt-6 mb-2" dangerouslySetInnerHTML={applyInlineFormatting(line.substring(4))} />);
      } else if (line.startsWith('**') && line.includes(':')) {
        elements.push(<p key={index} className="text-neutral-800 my-2" dangerouslySetInnerHTML={applyInlineFormatting(line)} />);
      } else if (line === '---') {
        elements.push(<hr key={index} className="my-4 border-neutral-200" />);
      } else if (line) {
        elements.push(<p key={index} className="text-neutral-700 mb-2" dangerouslySetInnerHTML={applyInlineFormatting(line)} />);
      }
    }
  });

  flushListItems(); // Flush any remaining list items at the end of the content

  return <div className="prose max-w-none">{elements}</div>;
};


const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ markdownContent }) => {
  return (
    <div className="space-y-4 animate-fade-in">
        <MarkdownParser content={markdownContent} />
    </div>
  );
};

export default ResultsDisplay;
