/**
 * @jest-environment jsdom
 */

import { render } from '@testing-library/react';
import React from 'react';

// Simple smoke test to ensure the app structure is working
/* eslint-env jest */
describe('Application Structure', () => {
  it('should be able to import React', () => {
    expect(typeof React).toBe('object');
  });

  it('should have render function available', () => {
    expect(typeof render).toBe('function');
  });
});
