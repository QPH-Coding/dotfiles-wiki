local map = require("core.keymaps").mapper("GrugFar")

require("grug-far").setup({})

map({ "n", "x" }, "<leader>sr", "<cmd>GrugFar<CR>", {
  desc = "Search and replace",
})
