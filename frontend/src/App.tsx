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
