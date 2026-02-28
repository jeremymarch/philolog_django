import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  List,
  type RowComponentProps,
  useListRef,
  type ListImperativeAPI,
} from "react-window";
import { useInfiniteLoader } from "react-window-infinite-loader";
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

interface PhiloListState {
  selectId: number;
  query: string;
  arrOptions: Map<number, string>;
}

interface PhiloListProps {
  onWordSelect: (id: number, lexicon: string) => void;
}

const LEXICON_LIMITS: Record<string, number> = {
  lsj: 116661,
  slater: 5281,
  ls: 51675,
};

const PhiloList = ({ onWordSelect }: PhiloListProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [lexicon, setLexiconState] = useState(() => {
    const savedLexicon = localStorage.getItem("lexicon");
    return savedLexicon || "lsj";
  });
  const [results, setResults] = useState<PhiloListState>({
    selectId: 0,
    query: "",
    arrOptions: new Map(),
  });
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
    setResults({ selectId: 0, query: "", arrOptions: new Map() });
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
          `query?query={"regex":0,"lexicon":"${currentLexicon}","tag_id":0,"root_id":0,"w":"${query}"}&n=101&idprefix=lemmata&x=0.17297130510758496&requestTime=1771393815484&page=0&mode=context`,
        );

        const newMap = new Map<number, string>();
        response.data.arrOptions.forEach(([id, word]) => {
          newMap.set(id, word);
        });

        setResults({
          selectId: response.data.selectId,
          query: response.data.query,
          arrOptions: newMap,
        });

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

  const itemCount = (LEXICON_LIMITS[lexicon] || 300000) + 1;
  const loadMoreItems = async (startIndex: number, stopIndex: number) => {
    if (isLoading) return;

    const limit = LEXICON_LIMITS[lexicon] || 300000;
    const actualStart = Math.max(1, startIndex);
    const actualEnd = Math.min(stopIndex, limit);

    if (actualStart > actualEnd) return;

    try {
      setIsLoading(true);
      const response = await axios.get<ResponseData>(
        `range?start=${actualStart}&end=${actualEnd}&lexicon=${lexicon}&requestTime=${Date.now()}`,
      );

      if (response.data.arrOptions && response.data.arrOptions.length > 0) {
        setResults((prev) => {
          const updatedMap = new Map(prev.arrOptions);
          response.data.arrOptions.forEach(([id, word]) => {
            updatedMap.set(id, word);
          });
          return {
            ...prev,
            arrOptions: updatedMap,
          };
        });
      }
    } catch (err) {
      console.error("Failed to load more items:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData(debouncedSearchTerm, lexicon);
  }, [debouncedSearchTerm, lexicon, fetchData]);

  useEffect(() => {
    if (
      results.query !== "" &&
      results.selectId !== undefined &&
      results.selectId !== null &&
      results.arrOptions.size > 0 &&
      listRef.current
    ) {
      listRef.current.scrollToRow({ index: results.selectId, align: "center" });
    }
  }, [results.query, results.selectId, results.arrOptions.size, listRef]);

  useEffect(() => {
    if (
      results.query === "" &&
      listRef.current &&
      results.arrOptions.size > 0
    ) {
      listRef.current.scrollToRow({ index: 1, align: "start" });
      setShouldScrollToTop(false);
    }
  }, [results.query, results.arrOptions.size, listRef]);

  useEffect(() => {
    if (
      shouldScrollToTop &&
      results.query === "" &&
      listRef.current &&
      results.arrOptions.size > 0
    ) {
      listRef.current.scrollToRow({ index: 1, align: "start" });
      setShouldScrollToTop(false);
    }
  }, [shouldScrollToTop, results.query, results.arrOptions.size, listRef]);

  // Handle input changes
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    let value = event.target.value;
    if (lexicon === "lsj" || lexicon === "slater") {
      value = transliterateToGreek(value);
    }
    setSearchTerm(value);
  };

  const handleKeyUp = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (selectedWordId !== null) {
        onWordSelect(selectedWordId, lexicon);
      }
    }
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
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (lexicon === "lsj") {
        setLexiconAndSave("ls");
      } else if (lexicon === "slater") {
        setLexiconAndSave("lsj");
      } else if (lexicon === "ls") {
        setLexiconAndSave("slater");
      }
      setSearchTerm("");
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      if (lexicon === "lsj") {
        setLexiconAndSave("slater");
      } else if (lexicon === "slater") {
        setLexiconAndSave("ls");
      } else if (lexicon === "ls") {
        setLexiconAndSave("lsj");
      }
      setSearchTerm("");
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (results.arrOptions.size === 0) return;

      event.preventDefault();

      let newIndex = -1;
      if (selectedWordId === null) {
        // Find the first loaded index in the map
        const loadedIndices = Array.from(results.arrOptions.keys()).sort(
          (a, b) => a - b,
        );
        newIndex = loadedIndices[0] || 1;
      } else {
        if (event.key === "ArrowDown") {
          newIndex = Math.min(selectedWordId + 1, itemCount - 1);
        } else {
          newIndex = Math.max(selectedWordId - 1, 1);
        }
      }

      if (newIndex !== -1) {
        setSelectedWordId(newIndex);
        if (listRef.current) {
          if (scrollOnEdge) {
            const listElement = listRef.current.element;
            if (listElement) {
              const rowHeight = 40; // From List component prop
              const clientHeight = listElement.clientHeight;
              const currentScrollTop = listElement.scrollTop;

              const firstVisibleIndex = Math.ceil(currentScrollTop / rowHeight);
              const lastVisibleIndex =
                Math.floor((currentScrollTop + clientHeight) / rowHeight) - 1;

              if (event.key === "ArrowDown") {
                if (newIndex >= lastVisibleIndex) {
                  listElement.scrollTop =
                    (newIndex + 2) * rowHeight - clientHeight;
                }
              } else if (event.key === "ArrowUp") {
                if (newIndex <= firstVisibleIndex) {
                  listElement.scrollTop = (newIndex - 1) * rowHeight;
                }
              }
            }
          } else {
            listRef.current.scrollToRow({ index: newIndex, align: "center" });
          }
        }
      }
    }
  };

  function PhiloListRowComponent({
    index,
    style,
  }: RowComponentProps<{
    results: PhiloListState;
  }>) {
    if (index === 0) return <div style={style} />;

    const word = results.arrOptions.get(index);
    if (word !== undefined) {
      const isSelected = index === selectedWordId;
      return (
        <div
          className={`philorow ${isSelected ? "selectedrow" : ""}`}
          data-wordid={index}
          data-lexicon={lexicon}
          style={style}
          onClick={() => {
            setSelectedWordId(index);
            onWordSelect(index, lexicon);
          }}
        >
          {word}
        </div>
      );
    } else {
      return (
        <div className="philorow" style={style}>
          ...
        </div>
      );
    }
  }

  const onRowsRendered = useInfiniteLoader({
    isRowLoaded: (index) => index === 0 || results.arrOptions.has(index),
    loadMoreRows: loadMoreItems,
    rowCount: itemCount,
    threshold: 30,
    minimumBatchSize: 100,
  });

  return (
    <div
      className={`philolistcontainer ${lexicon}`}
      onClick={() => {
        inputRef.current?.focus();
      }}
    >
      <div className="philobuttons">
        <input
          type="radio"
          name="lexicon-select"
          value="lsj"
          id="lsj-radio"
          checked={lexicon === "lsj"}
          onChange={() => {
            setLexiconAndSave("lsj");
            //setSearchTerm("");
          }}
          tabIndex={-1}
        />
        <label htmlFor="lsj-radio">LSJ</label>
        <input
          type="radio"
          name="lexicon-select"
          value="slater"
          id="slater-radio"
          checked={lexicon === "slater"}
          onChange={() => {
            setLexiconAndSave("slater");
            //setSearchTerm("");
          }}
          tabIndex={-1}
        />
        <label htmlFor="slater-radio">Slater</label>
        <input
          type="radio"
          name="lexicon-select"
          value="ls"
          id="ls-radio"
          checked={lexicon === "ls"}
          onChange={() => {
            setLexiconAndSave("ls");
            //setSearchTerm("");
          }}
          tabIndex={-1}
        />
        <label htmlFor="ls-radio">Lewis & Short</label>
      </div>
      <input
        ref={inputRef}
        className="philosearch"
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onKeyUp={handleKeyUp}
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
        onRowsRendered={onRowsRendered}
        rowProps={{ results }}
        rowComponent={PhiloListRowComponent}
        rowCount={itemCount}
        rowHeight={(index) => (index === 0 ? 0 : 40)}
        style={{ width: 260, height: "calc(100% - 120px)" }}
        className="philolist no-scrollbars"
      />
    </div>
  );
};

export default PhiloList;
