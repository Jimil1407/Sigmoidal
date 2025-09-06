/*
  Warnings:

  - You are about to drop the column `stockId` on the `Position` table. All the data in the column will be lost.
  - Added the required column `stockSymbol` to the `Position` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "Position" DROP CONSTRAINT "Position_stockId_fkey";

-- AlterTable
ALTER TABLE "Position" DROP COLUMN "stockId",
ADD COLUMN     "stockSymbol" TEXT NOT NULL;

-- AddForeignKey
ALTER TABLE "Position" ADD CONSTRAINT "Position_stockSymbol_fkey" FOREIGN KEY ("stockSymbol") REFERENCES "Stock"("symbol") ON DELETE RESTRICT ON UPDATE CASCADE;
