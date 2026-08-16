import './Header.css';

interface HeaderProps {
  hasGame: boolean;
  onLogoClick: () => void;
}

export function Header({ hasGame, onLogoClick }: HeaderProps) {
  return (
    <header className="header">
      <button className="header-logo" onClick={onLogoClick} aria-label="Mingle home">
        <span className="header-logo-text">mingle</span>
        <span className="header-version">v0.1</span>
      </button>
      {hasGame && (
        <span className="header-tag">tic-tac-toe</span>
      )}
    </header>
  );
}
