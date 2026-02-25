import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  List,
  type RowComponentProps,
  useListRef,
  type ListImperativeAPI,
} from "react-window";
import axios from "axios";
import { useDebounce } from "./useDebounce";

type PhiloRowItem = [number, string];

// {
//   "selectId": 110755,
//     "error": "",
//     "wtprefix": "lemmata",
//     "nocache": 0,
//     "container": "lemmataContainer",
//     "requestTime": 1771459324274,
//     "page": 0,
//     "lastPage": 0,
//     "lastPageUp": 0,
//       "query": "φερ",
//     "arrOptions": [[110654, "φατνωτός"], [110655, "φατός"

interface ResponseData {
  selectId: number;
  error: string;
  wtprefix: string;
  nocache: number;
  container: string;
  requestTime: number;
  page: number;
  lastPage: number;
  lastPageUp: number;
  query: string;
  arrOptions: Array<PhiloRowItem>;
}

interface PhiloListProps {
  onWordSelect: (id: number, lexicon: string) => void;
}

const PhiloList = ({ onWordSelect }: PhiloListProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [lexicon, setLexiconState] = useState(() => {
    const savedLexicon = localStorage.getItem("lexicon");
    return savedLexicon || "lsj";
  });
  const [results, setResults] = useState<ResponseData>();
  const [isLoading, setIsLoading] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [error, setError] = useState<string | null>(null);
  const [selectedWordId, setSelectedWordId] = useState<number | null>(null);
  const [shouldScrollToTop, setShouldScrollToTop] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [scrollOnEdge, setScrollOnEdge] = useState(true); // New state variable

  const setLexiconAndSave = (newLexicon: string) => {
    setLexiconState(newLexicon);
    localStorage.setItem("lexicon", newLexicon);
  };

  const debouncedSearchTerm = useDebounce(searchTerm, 350);
  const listRef = useListRef(null as unknown as ListImperativeAPI);
  const inputRef = useRef<HTMLInputElement>(null);
  const onWordSelectRef = useRef(onWordSelect);

  useEffect(() => {
    onWordSelectRef.current = onWordSelect;
  }, [onWordSelect]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const transliterateToGreek = (text: string) => {
    const map: { [key: string]: string } = {
      a: "α",
      b: "β",
      c: "ψ",
      g: "γ",
      d: "δ",
      e: "ε",
      z: "ζ",
      h: "η",
      q: "θ",
      i: "ι",
      k: "κ",
      l: "λ",
      m: "μ",
      n: "ν",
      j: "ξ",
      o: "ο",
      p: "π",
      r: "ρ",
      s: "σ",
      t: "τ",
      u: "θ",
      v: "ω",
      f: "φ",
      x: "χ",
      y: "υ",
      w: "ς",
    };
    return text
      .toLowerCase()
      .split("")
      .map((char) => map[char] || char)
      .join("");
  };

  const fetchData = useCallback(
    async (query: string, currentLexicon: string) => {
      setSelectedWordId(null);
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.get<ResponseData>(
          `query?&query=%7B%22regex%22%3A0%2C%22lexicon%22%3A%22${currentLexicon}%22%2C%22tag_id%22%3A0%2C%22root_id%22%3A0%2C%22w%22%3A%22${query}%22%7D&n=101&idprefix=lemmata&x=0.17297130510758496&requestTime=1771393815484&page=0&mode=context`,
        );
        setResults(response.data);

        if (response.data.selectId !== null && response.data.query !== "") {
          setSelectedWordId(response.data.selectId);
          onWordSelectRef.current(response.data.selectId, currentLexicon);
        }
      } catch (err) {
        setError("Failed to fetch data");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    fetchData(debouncedSearchTerm, lexicon);
  }, [debouncedSearchTerm, lexicon, fetchData]);

  useEffect(() => {
    if (
      results?.query !== "" &&
      results?.selectId !== undefined &&
      results.selectId !== null &&
      results.arrOptions &&
      listRef.current
    ) {
      const index = results.arrOptions.findIndex(
        (item) => item[0] === results.selectId,
      );
      if (index !== -1) {
        listRef.current.scrollToRow({ index, align: "center" });
      }
    }
  }, [results, listRef]);

  useEffect(() => {
    if (
      results?.query === "" &&
      listRef.current &&
      (results?.arrOptions?.length ?? 0) > 0
    ) {
      listRef.current.scrollToRow({ index: 0, align: "start" });
      setShouldScrollToTop(false);
    }
  }, [results, listRef]);

  useEffect(() => {
    if (
      shouldScrollToTop &&
      results?.query === "" &&
      listRef.current &&
      (results?.arrOptions?.length ?? 0) > 0
    ) {
      listRef.current.scrollToRow({ index: 0, align: "start" });
      setShouldScrollToTop(false);
    }
  }, [shouldScrollToTop, results, listRef]);

  // Handle input changes
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let value = event.target.value;
    if (lexicon === "lsj" || lexicon === "slater") {
      value = transliterateToGreek(value);
    }
    setSearchTerm(value);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Escape") {
      setSearchTerm("");
      setShouldScrollToTop(true);
    } else if (event.key === "1") {
      event.preventDefault();
      setLexiconAndSave("lsj");
      setSearchTerm("");
    } else if (event.key === "2") {
      event.preventDefault();
      setLexiconAndSave("slater");
      setSearchTerm("");
    } else if (event.key === "3") {
      event.preventDefault();
      setLexiconAndSave("ls");
      setSearchTerm("");
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (!results || !results.arrOptions || results.arrOptions.length === 0)
        return;

      event.preventDefault();

      let newIndex = -1;
      if (selectedWordId === null) {
        newIndex = 0;
      } else {
        const currentIndex = results.arrOptions.findIndex(
          (item) => item[0] === selectedWordId,
        );
        if (currentIndex === -1) {
          newIndex = 0;
        } else {
          if (event.key === "ArrowDown") {
            newIndex = Math.min(
              currentIndex + 1,
              results.arrOptions.length - 1,
            );
          } else {
            newIndex = Math.max(currentIndex - 1, 0);
          }
        }
      }

      if (newIndex !== -1) {
        const [newWordId] = results.arrOptions[newIndex];
        setSelectedWordId(newWordId);
        onWordSelect(newWordId, lexicon);
        if (listRef.current) {
          if (scrollOnEdge) {
            const listElement = listRef.current.element;
            if (listElement) {
              const rowHeight = 40; // From List component prop
              const clientHeight = listElement.clientHeight;
              const currentScrollTop = listElement.scrollTop;

              const firstVisibleIndex = Math.floor(
                currentScrollTop / rowHeight,
              );
              const lastVisibleIndex =
                Math.floor((currentScrollTop + clientHeight) / rowHeight) - 1;

              if (event.key === "ArrowDown") {
                // If new selection is below the second-to-last visible row
                if (newIndex > lastVisibleIndex - 1) {
                  listElement.scrollTop += rowHeight;
                }
              } else if (event.key === "ArrowUp") {
                // If new selection is above the second visible row
                if (newIndex < firstVisibleIndex + 1) {
                  listElement.scrollTop -= rowHeight;
                }
              }
            }
          } else {
            // Original behavior: always scroll to center
            listRef.current.scrollToRow({ index: newIndex, align: "center" });
          }
        }
      }
    }
  };

  function PhiloListRowComponent({
    index,
    results,
    style,
  }: RowComponentProps<{
    results: ResponseData | undefined;
  }>) {
    if (results !== undefined) {
      const wordId = results.arrOptions[index][0];
      const isSelected = wordId === selectedWordId;
      return (
        <div
          className={`philorow ${isSelected ? "selectedrow" : ""}`}
          data-wordid={wordId}
          data-lexicon={lexicon}
          style={style}
          onClick={() => {
            setSelectedWordId(wordId);
            onWordSelect(wordId, lexicon);
          }}
        >
          {results.arrOptions[index][1]}
        </div>
      );
    } else {
      return null;
    }
  }

  return (
    <div
      className={`philolistcontainer ${lexicon}`}
      onClick={() => {
        inputRef.current?.focus();
      }}
    >
      <div className="philobuttons">
        <button
          onClick={() => {
            setLexiconAndSave("lsj");
            setSearchTerm("");
          }}
          disabled={lexicon === "lsj"}
          className={lexicon === "lsj" ? "active" : ""}
        >
          LSJ
        </button>
        <button
          onClick={() => {
            setLexiconAndSave("slater");
            setSearchTerm("");
          }}
          disabled={lexicon === "slater"}
          className={lexicon === "slater" ? "active" : ""}
        >
          Slater
        </button>
        <button
          onClick={() => {
            setLexiconAndSave("ls");
            setSearchTerm("");
          }}
          disabled={lexicon === "ls"}
          className={lexicon === "ls" ? "active" : ""}
        >
          Lewis & Short
        </button>
      </div>
      <input
        ref={inputRef}
        className="philosearch"
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
      />
      {isLoading && (
        <div id="lemmataloading">
          <div className="lds-spinner">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
        </div>
      )}
      <List
        listRef={listRef}
        rowProps={{ results }}
        rowComponent={PhiloListRowComponent}
        rowCount={results?.arrOptions?.length ?? 0}
        rowHeight={40}
        style={{ width: 260, height: "calc(100% - 120px)" }}
        className="philolist"
      />
    </div>
  );
};

export default PhiloList;
