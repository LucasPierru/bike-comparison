import { NextFunction, Request, Response } from 'express';
import 'dotenv/config';

const API_KEY = process.env.API_KEY;

export const authorizeRequest = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const apiKey = req.headers['x-api-key'];

  // If origin is not allowed, check for API key
  if (apiKey === API_KEY) {
    return next();
  }

  // If neither is valid, return an error
  res
    .status(403)
    .json({ error: 'Forbidden: Invalid origin or API key required' });
};
