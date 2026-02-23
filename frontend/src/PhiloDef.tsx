import { useState, useEffect } from "react";
import axios from "axios";

interface PhiloDefProps {
  wordId: number | null;
  lexicon: string | null;
}

const PhiloDef = ({ wordId, lexicon }: PhiloDefProps) => {
  const [definition, setDefinition] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (wordId === null || wordId < 1 || lexicon === null) {
      setDefinition(null);
      return;
    }

    const fetchDefinition = async () => {
      setLoading(true);
      setError(null);
      try {
        //https://philolog.us/lsj/item?id=10&lexicon=lsj&skipcache=0&addwordlinks=0&x=0.9559306530260945
        const response = await axios.get(
          `item?id=${wordId}&lexicon=${lexicon}&skipcache=0&addwordlinks=0&x=0.9559306530260945`,
        );
        setDefinition(response.data.def);
      } catch (err) {
        console.error("Failed to fetch definition:", err);
        setError("Failed to load definition.");
      } finally {
        setLoading(false);
      }
    };

    fetchDefinition();
  }, [wordId, lexicon]);

  return (
    <div className="philodefcontainer">
      <div
        className="philodef"
        dangerouslySetInnerHTML={{
          __html: loading ? "Loading..." : error ? "" : definition || "",
        }}
      />
    </div>
  );
};

export default PhiloDef;
