// components/MarketIntelligence.test.js
import { render, screen } from '@testing-library/react';
import GlobalMarketIntelligence from './GlobalMarketIntelligence';

test('Vérifie si le composant de test existe', () => {
  render(<GlobalMarketIntelligence />);
  // Ce test échouera jusqu'à ce que ton composant soit lié à l'API
  console.log("✅ Structure de test créée. Prêt à tester l'API.");
});