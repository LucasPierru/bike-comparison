import { Brand } from "./brand.types";
import { Common } from "./common.type";

export type AffiliateLink = {
  base_url: string;
  color: string;
};

export type Variation = {
  color: string;
  sizes: string[];
};

export type Bike = {
  affiliateLink: AffiliateLink;
  name: string;
  description: string;
  brand: Brand;
  type: string;
  currentPrice: number;
  currency: string;
  imageUrl: string;
  source: string;
  weight: string;
  weightLimit: string;
  variations: Variation[];
} & Common;
