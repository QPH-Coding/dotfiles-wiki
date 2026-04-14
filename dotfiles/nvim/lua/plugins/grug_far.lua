require("grug-far").setup({})

vim.keymap.set({ "n", "x" }, "<leader>sr", "<cmd>GrugFar<CR>", {
  desc = "Search and replace",
})
