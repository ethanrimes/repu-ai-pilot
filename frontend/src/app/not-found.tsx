import Link from 'next/link';

export default function NotFound() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <h1>404 - Page Not Found</h1>
      <p>Sorry, the page you are looking for does not exist.</p>
      <Link href="/" style={{
        padding: '0.5rem 1rem',
        background: '#3b82f6',
        color: 'white',
        textDecoration: 'none',
        borderRadius: '4px'
      }}>
        Go Back Home
      </Link>
    </div>
  );
}