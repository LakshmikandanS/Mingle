import './Header.css';

interface HeaderProps {
  hasGame: boolean;
  onLogoClick: () => void;
  gameTag?: string;
}

export function Header({ hasGame, onLogoClick, gameTag }: HeaderProps) {
  return (
    <header className="header">
      <button className="header-logo" onClick={onLogoClick} aria-label="Mingle home">
        <span className="header-logo-text">mingle</span>
        <span className="header-version">v0.1</span>
      </button>
      {hasGame && gameTag && (
        <span className="header-tag">{gameTag}</span>
      )}
    </header>
  );
}
