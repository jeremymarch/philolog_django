
import { useState, useEffect } from "react";
import "./SettingsMenu.css";

const SettingsMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [theme, setTheme] = useState("system");

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "system";
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, []);

  const applyTheme = (selectedTheme: string) => {
    const htmlEl = document.documentElement;
    htmlEl.classList.remove("dark", "light");
    if (selectedTheme === "dark") {
      htmlEl.classList.add("dark");
    } else if (selectedTheme === "light") {
      htmlEl.classList.add("light");
    }
  };

  const handleThemeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTheme = e.target.value;
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
  };

  return (
    <div id="hamburgercontainer">
      <svg
        id="hamburger"
        viewBox="0 0 120 120"
        onClick={() => setIsOpen(!isOpen)}
      >
        <rect x="10" y="30" width="100" height="12"></rect>
        <rect x="10" y="56" width="100" height="12"></rect>
        <rect x="10" y="82" width="100" height="12"></rect>
      </svg>
      {isOpen && (
        <div className="settings-modal">
          <div className="theme-options">
            <h4>Theme</h4>
            <label>
              <input
                type="radio"
                name="theme"
                value="light"
                checked={theme === "light"}
                onChange={handleThemeChange}
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
              />{" "}
              System
            </label>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsMenu;
