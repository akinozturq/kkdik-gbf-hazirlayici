import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Header from './components/Header';
import ProductList from './components/ProductList/ProductList';
import WizardLayout from './components/Wizard/WizardLayout';

function MainContent() {
  const { currentView } = useApp();

  return (
    <div className="app-container">
      <Header />
      {currentView === 'list' && <ProductList />}
      {currentView === 'wizard' && <WizardLayout />}
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <MainContent />
    </AppProvider>
  );
}
