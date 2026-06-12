import { render, screen, waitFor } from '@testing-library/react';
import GlobalMarketIntelligence from './GlobalMarketIntelligence';

// 1. On simule la réponse de ton API Render
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ 
      fear_greed: { score: 27, rating: 'fear' } 
    }),
  })
);

test('Le composant affiche le score 27 reçu du backend', async () => {
  render(<GlobalMarketIntelligence />);
  
  // 2. On attend que l'API soit appelée et que le score soit injecté dans le DOM
  await waitFor(() => {
    // Vérifie que le score 27 est bien présent dans le composant
    expect(screen.getByText(/27/i)).toBeInTheDocument();
  });
  
  console.log("✅ Test Frontend : Intégration API validée.");
});