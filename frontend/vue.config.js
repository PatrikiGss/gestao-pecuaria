const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 7777,
  },

  // Nome exibido na aba do navegador. Sem esta linha o titulo vinha do
  // 'name' do package.json e a aba dizia apenas "frontend".
  chainWebpack: (config) => {
    config.plugin('html').tap((args) => {
      args[0].title = 'Projeto AORUS'
      return args
    })
  },

  // Nome do app instalado (o plugin de PWA gera o manifest a partir daqui).
  pwa: {
    name: 'Projeto AORUS',
    themeColor: '#237837',
  },
})
