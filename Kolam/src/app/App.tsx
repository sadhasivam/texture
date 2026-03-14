import '../styles/tokens.css';
import { Providers } from './providers';
import DashboardPage from '../pages/DashboardPage';

function App() {
  return (
    <Providers>
      <DashboardPage />
    </Providers>
  );
}

export default App;
