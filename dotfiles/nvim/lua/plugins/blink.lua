require("blink.cmp").setup({
  keymap = { preset = "default" },
  appearance = {
    nerd_font_variant = "mono",
  },
  completion = {
    documentation = { auto_show = false },
  },
  sources = {
    default = { "lsp", "path", "buffer" },
  },
  fuzzy = {
    implementation = "lua",
  },
})

return {
  capabilities = require("blink.cmp").get_lsp_capabilities(),
}
