// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITokenMu {
    event CellAuthorized(address indexed cell);
    event CellRevoked(address indexed cell);
    event PremiumPaid(address indexed from, uint256 amount);
    event CapitalWithdrawn(address indexed cell, uint256 amount);

    function authorizeCell(address cell) external;
    function revokeCell(address cell) external;
    function isCellAuthorized(address cell) external view returns (bool);
    function burnForPremium(address from, uint256 amount) external;
    function mintForClaim(address to, uint256 amount) external;
    function getMinimumCapitalRequirement() external view returns (uint256);
}