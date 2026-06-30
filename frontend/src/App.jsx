import EvidencePanel from "./components/EvidencePanel.jsx";
import ReleasePackageEditor from "./components/ReleasePackageEditor.jsx";
import RetrievedDocsPanel from "./components/RetrievedDocsPanel.jsx";
import ValidationPanel from "./components/ValidationPanel.jsx";

export default function App() {
  return (
    <main>
      <h1>Release Documentation Agent</h1>
      <ReleasePackageEditor />
      <EvidencePanel />
      <RetrievedDocsPanel />
      <ValidationPanel />
    </main>
  );
}
