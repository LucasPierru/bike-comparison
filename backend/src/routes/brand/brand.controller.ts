import { Request, Response } from 'express';
import Brand from '../../models/brand.mongo';

export const httpGetBrands = async (req: Request, res: Response) => {
  try {
    const brands = await Brand.find();
    res.status(200).json({ brands });
  } catch (error) {
    res
      .status(500)
      .json({ message: `Cannot access brands ${req.params.id}`, error });
  }
};

export const httpSearchBrand = async (req: Request, res: Response) => {
  const { searchQuery } = req.query;

  try {
    const brand = await Brand.findOne({
      $text: { $search: searchQuery as string }
    });
    res.status(200).json({ brand });
  } catch (error) {
    res.status(500).json({ message: `Cannot access bikes`, error });
  }
};
