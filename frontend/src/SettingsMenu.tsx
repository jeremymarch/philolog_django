import { useState, useEffect, useRef } from "react";
import "./SettingsMenu.css";

const SettingsMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [theme, setTheme] = useState("system");
  const selectedOptionRef = useRef<HTMLInputElement>(null);
  const hamburgerRef = useRef<HTMLButtonElement>(null);
  const wasOpen = useRef(isOpen);

  useEffect(() => {
    if (isOpen && selectedOptionRef.current) {
      selectedOptionRef.current.focus();
    } else if (!isOpen && wasOpen.current) {
      hamburgerRef.current?.focus();
    }
    wasOpen.current = isOpen;
  }, [isOpen]);

  useEffect(() => {
    // Apply "system" theme initially to ensure a clean state
    applyTheme("system");

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      setTheme(savedTheme); // Update state to saved theme
      applyTheme(savedTheme); // Apply saved theme
    } else {
      // If no saved theme, "system" is already the state and applied.
      // We explicitly save "system" to localStorage so it's consistent for next loads
      localStorage.setItem("theme", "system");
    }
  }, []); // Run only once on mount

  const applyTheme = (selectedTheme: string) => {
    const htmlEl = document.documentElement;
    htmlEl.classList.remove("dark", "light");
    if (
      (window.matchMedia("(prefers-color-scheme: dark)").matches &&
        selectedTheme !== "light") ||
      selectedTheme === "dark"
    ) {
      htmlEl.classList.add("dark");
    } else {
      htmlEl.classList.remove("dark");
    }
  };

  const handleThemeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTheme = e.target.value;
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      e.stopPropagation();
      setIsOpen(false);
    }
  };

  return (
    <div id="hamburgercontainer">
      <button
        id="hamburger"
        ref={hamburgerRef}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Settings"
      >
        <svg viewBox="0 0 120 120">
          <rect x="10" y="30" width="100" height="12"></rect>
          <rect x="10" y="56" width="100" height="12"></rect>
          <rect x="10" y="82" width="100" height="12"></rect>
        </svg>
      </button>
      {isOpen && (
        <div className="click-cover" onClick={() => setIsOpen(false)}>
          <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
            <div className="theme-options">
              <h4>Theme</h4>
              <label>
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  checked={theme === "light"}
                  onChange={handleThemeChange}
                  onKeyDown={handleKeyDown}
                  ref={theme === "light" ? selectedOptionRef : null}
                />{" "}
                Light
              </label>
              <label>
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  checked={theme === "dark"}
                  onChange={handleThemeChange}
                  onKeyDown={handleKeyDown}
                  ref={theme === "dark" ? selectedOptionRef : null}
                />{" "}
                Dark
              </label>
              <label>
                <input
                  type="radio"
                  name="theme"
                  value="system"
                  checked={theme === "system"}
                  onChange={handleThemeChange}
                  onKeyDown={handleKeyDown}
                  ref={theme === "system" ? selectedOptionRef : null}
                />{" "}
                System
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsMenu;
