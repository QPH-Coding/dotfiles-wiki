local map = require("core.keymaps").mapper("Persistence")
local session_options = vim.tbl_filter(function(option)
  return option ~= "terminal"
end, vim.opt.sessionoptions:get())

require("persistence").setup({
  need = 1,
  branch = true,
  options = session_options,
})

map("n", "<leader>qs", function()
  require("persistence").load()
end, { desc = "Restore session for cwd" })

map("n", "<leader>qS", function()
  require("persistence").select()
end, { desc = "Select session" })

map("n", "<leader>ql", function()
  require("persistence").load({ last = true })
end, { desc = "Restore last session" })

map("n", "<leader>qd", function()
  require("persistence").stop()
end, { desc = "Stop session saving" })
