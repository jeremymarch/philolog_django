import { useState } from "react";
import "./App.css";
import PhiloList from "./PhiloList";
import PhiloDef from "./PhiloDef";

function App() {
  const [selectedWord, setSelectedWord] = useState<{
    id: number;
    lexicon: string;
  } | null>(null);

  return (
    <>
      <div id="logocontainer">
        <div id="logo">philolog.us</div>
        <div id="hamburgercontainer">
          <svg id="hamburger" viewBox="0 0 120 120">
            <rect x="10" y="30" width="100" height="12"></rect>
            <rect x="10" y="56" width="100" height="12"></rect>
            <rect x="10" y="82" width="100" height="12"></rect>
          </svg>
        </div>
      </div>
      <PhiloList
        onWordSelect={(id, lexicon) => setSelectedWord({ id, lexicon })}
      />
      <PhiloDef
        wordId={selectedWord?.id ?? null}
        lexicon={selectedWord?.lexicon ?? null}
      />
    </>
  );
}

export default App;
