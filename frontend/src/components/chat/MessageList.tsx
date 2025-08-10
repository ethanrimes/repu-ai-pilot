import ReactMarkdown from 'react-markdown';
import styles from '@/styles/chat.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className={styles.messageList}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`${styles.message} ${styles[message.role]}`}
        >
          <div className={styles.messageContent}>
            {message.role === 'assistant' ? (
              <ReactMarkdown
                components={{
                  // Custom styling for markdown elements
                  p: ({ children }) => <p className={styles.markdownP}>{children}</p>,
                  ul: ({ children }) => <ul className={styles.markdownUl}>{children}</ul>,
                  ol: ({ children }) => <ol className={styles.markdownOl}>{children}</ol>,
                  li: ({ children }) => <li className={styles.markdownLi}>{children}</li>,
                  strong: ({ children }) => <strong className={styles.markdownStrong}>{children}</strong>,
                  em: ({ children }) => <em className={styles.markdownEm}>{children}</em>,
                  code: ({ children, className }) => {
                    const isInline = !className;
                    return isInline ? (
                      <code className={styles.markdownInlineCode}>{children}</code>
                    ) : (
                      <code className={styles.markdownCodeBlock}>{children}</code>
                    );
                  },
                  pre: ({ children }) => <pre className={styles.markdownPre}>{children}</pre>,
                  blockquote: ({ children }) => <blockquote className={styles.markdownBlockquote}>{children}</blockquote>,
                  h1: ({ children }) => <h1 className={styles.markdownH1}>{children}</h1>,
                  h2: ({ children }) => <h2 className={styles.markdownH2}>{children}</h2>,
                  h3: ({ children }) => <h3 className={styles.markdownH3}>{children}</h3>,
                  a: ({ children, href }) => (
                    <a href={href} target="_blank" rel="noopener noreferrer" className={styles.markdownLink}>
                      {children}
                    </a>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            ) : (
              // User messages don't need markdown parsing
              message.content
            )}
          </div>
          <div className={styles.messageTime}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      ))}
    </div>
  );
}