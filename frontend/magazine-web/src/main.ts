import { bootstrapApplication } from '@angular/platform-browser';

import { appConfig } from './app/app.config';
import { App } from './app/app';
import { API_BASE_URL } from './app/core/api.tokens';
import { loadApiBaseUrl } from './app/core/load-api-base';

loadApiBaseUrl()
  .then((apiBaseUrl) =>
    bootstrapApplication(App, {
      providers: [...appConfig.providers, { provide: API_BASE_URL, useValue: apiBaseUrl }]
    })
  )
  .catch((err) => console.error(err));
