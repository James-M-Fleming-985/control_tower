import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './components/Landing';
import RequestPage from './pages/RequestPage';
import ResponsePage from './pages/ResponsePage';

function App() {
  useEffect(() => {
    console.log('📊 Feedback360 - Ready');
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/request" element={<RequestPage />} />
        <Route path="/respond" element={<ResponsePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
